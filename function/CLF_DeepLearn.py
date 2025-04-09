"""
Stacked RandomForest Classifier :
Load Train
Train CLF
Load test
Copy Test to Output Path
Prediction
    Optional : 2 step CLF (Simple Map + RFC)
return df + ['Category'] +['Type']
"""

import pickle
from .clf_func import *
from datasets import Dataset as HFDataset, DatasetDict
from transformers import (
    RobertaTokenizer,
    RobertaForSequenceClassification,
    Trainer,
    TrainingArguments,
)
import torch
from dateutil.relativedelta import relativedelta
import sys
from .log_func import *

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def tokenize_sentences(sentences, tokenizer, max_length=24):
    return tokenizer(
        sentences,
        padding="max_length",
        truncation=True,
        max_length=max_length,
        return_tensors="pt",
    )


def get_dataset(tokenized_data, labels=None):
    data = {key: val for key, val in tokenized_data.items()}
    if labels is not None:
        data["labels"] = labels
    return HFDataset.from_dict(data)


def DL_clf(
    clf_config: dict,
    col_dfs: dict,
    train_excels: dict,
    output_paths: dict,
    excel_paths: dict,
    test_data_dict: dict,
    json_output: dict,
    dealergroup_path: str,
    acc_folder: str,
):
    try:
        print(">>>>>Classification : DeepLearn Classification Starts.\n")

        ###* clean train // remove data older than 2years
        train_df = merge_train(excel_paths, train_excels, clf_config["data_sheetname"])
        two_years_ago = datetime(
            (datetime.today() + relativedelta(years=-1)).year, 1, 1
        )
        train_df["Post Date"] = pd.to_datetime(train_df["Post Date"])
        train_df = train_df.loc[train_df["Post Date"] >= two_years_ago]
        train_df = train_df.rename(columns={"Source": "Source Name"})

        # * Type_col
        if clf_config["enable_Type_col"]:
            cate_type_map = train_df.set_index(["Category"])["Type"].to_dict()

        print("Cleasing of training data starts")
        train_df = cleanse_col(train_df)

        ###* Col mapping // get Category Mapping against provided col
        if clf_config["enable_col_mapping"]:
            cate_map, info = get_cate_map(
                train_df, clf_config["clf_option"], clf_config["enable_col_mapping"]
            )
            # * Remove Rows with values in cate_map
            train_df, _ = split_by_col_cate_dict(
                train_df, clf_config["enable_col_mapping"], cate_map
            )

        train_df = filter_minority(train_df, 2)

        # * load label encoder
        deeplearn_path = os.path.join(dealergroup_path, "DL_model", acc_folder, "model")
        label_encoder_path = os.path.join(deeplearn_path, "label_encoder.pkl")
        with open(label_encoder_path, "rb") as file:
            y_encoder = pickle.load(file)
        # * Check classes in both end
        if len(y_encoder.classes_) != len(set(train_df["Category"])):
            info = f"FATAL: {acc_folder} DeepLearn -  Label Encoder classes and train_df classes are not same\nScript Continues"
            json_output["LOG"].append(info)
            train_df = train_df[train_df["Category"].isin(y_encoder.classes_)]

        y = y_encoder.transform(train_df["Category"])

        ###setup model

        tokenizer = RobertaTokenizer.from_pretrained("roberta-base")
        model = RobertaForSequenceClassification.from_pretrained(
            "roberta-base", num_labels=len(y_encoder.classes_)
        )
        training_args = TrainingArguments(
            output_dir="DeepLearn",
            per_device_train_batch_size=512,
            evaluation_strategy="epoch",  # Evaluate at the end of each epoch
            logging_strategy="epoch",  # Log training information at the end of each epoch
            save_strategy="epoch",  # Align with evaluation strategy
            metric_for_best_model="eval_loss",  # Specify which metric to monitor
            weight_decay=0.01,  # L2 ridge regularization
            save_total_limit=5,
        )

        model_state_path = os.path.join(deeplearn_path, "model_state.pth")
        if device.type == "cpu":
            state = torch.load(model_state_path, map_location="cpu")
        else:
            state = torch.load(model_state_path)
        model.load_state_dict(state["state_dict"])
        loaded_trainer = Trainer(
            model=model,
            args=training_args,
        )

        dfs = {}
        for store in output_paths.keys():
            test_data_csv = test_data_dict[store]
            df = pd.read_csv(excel_paths[test_data_csv])

            if clf_config["enable_find_dept"]:
                df.Department = df.Department.fillna(
                    find_dept(df["Account Number"], df.Department)
                )

            df = fix_col_by_coltbl(df, col_dfs, "ExtractedData_to_CLF")
            df["store"] = store
            df_cleansed = cleanse_col(df)
            df["Post Date"] = pd.to_datetime(df["Post Date"]).dt.strftime("%Y-%m-%d")

            ###2stage clf
            if clf_config["enable_col_mapping"]:
                df_cleansed, df_match = split_by_col_cate_dict(
                    df_cleansed, clf_config["enable_col_mapping"], cate_map
                )

            df["Category"] = np.nan

            if len(df_cleansed) > 0:
                df_cleansed["Category"] = np.nan
                X = txtColumnSelector(
                    base_col="Description",
                    extra_cols=clf_config["join_text_columns__extra_cols"],
                ).transform(df_cleansed)

                tokenized_X = tokenize_sentences(X.tolist(), tokenizer)

                dataset = get_dataset(tokenized_X)

                results = loaded_trainer.predict(dataset)
                probabilities = torch.softmax(torch.tensor(results.predictions), dim=-1)
                class_labels = torch.argmax(probabilities, dim=-1)

                y_hat = y_encoder.inverse_transform(class_labels)
                df_cleansed["Category"] = y_hat
                df["Category"] = df["Category"].fillna(df_cleansed["Category"])

            # * Col Mapping
            if clf_config["enable_col_mapping"] and len(df_match) > 0:
                df_match["Category"] = df_match[clf_config["enable_col_mapping"]].map(
                    cate_map
                )
                df["Category"] = df["Category"].fillna(df_match["Category"])

            # * Type_col
            df["Type"] = np.nan

            if clf_config["enable_Type_col"]:
                df["Type"] = Type_col_mapping(
                    df["Category"],
                    cate_type_map,
                    clf_config["default_Type_value"],
                )

            # * Check for Nan in Category
            if df["Category"].isnull().sum() > 0:

                info = (
                    f"ERROR: {clf_config['acc_name_short']};{store} - Nan in Category"
                )
                json_output["LOG"].append(info)

            dfs[store] = df
        return dfs, json_output
    except Exception:
        e = get_error_info()

        info = f"FATAL: {clf_config['acc_name_short']}\n{e}"
        json_output["LOG"].append(info)
        return json_output
