"""
Simple RandomForest Classifier :
Load Train
Train CLF
Load test
Copy Test to Output Path
Prediction
    Optional : 2 step CLF (Simple Map + RFC)
return df + ['Category'] +['Type']
"""

import pandas as pd
from .clf_func import *
from .clf_func import (
    ZeroArrayTransformer,
    FunctionTransformer,
    FeatureUnion,
    CountVectorizer,
    ColumnTransformer,
    StandardScaler,
)
from sklearn.ensemble import RandomForestClassifier
from dateutil.relativedelta import relativedelta
from .log_func import *


def rfc_clf(
    clf_config: dict,
    col_dfs: dict,
    train_excels: dict,
    output_paths: dict,
    excel_paths: dict,
    test_data_dict: dict,
    json_output: dict,
):
    try:
        print(">>>>>Classification : Simple RFC Classification Starts.\n")

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

        y, y_encoder = get_y(train_df)

        # * word vectorizor
        vectorizor_option = {"count": CountVectorizer(), "tfidf": TfidfVectorizer()}
        vectorizor = vectorizor_option[clf_config["txt_vectorizor"]]

        # * Scaler
        if clf_config["StandardScaler"]:
            scaler = StandardScaler()
            scaler_col = clf_config["StandardScaler"]
        else:
            scaler = ZeroArrayTransformer()
            scaler_col = "Amount"

        txt_pipeline = imblearn.pipeline.Pipeline(
            [
                (
                    "col_selector",
                    txtColumnSelector(
                        base_col="Description",
                        extra_cols=clf_config["join_text_columns__extra_cols"],
                    ),
                ),
                ("vectorizor", vectorizor),
            ]
        )

        label_pipeline = imblearn.pipeline.Pipeline(
            [("labels", FunctionTransformer(get_labels_v2))]
        )

        amt_pipeline = imblearn.pipeline.Pipeline(
            [
                (
                    "amt_selector",
                    ColumnTransformer(
                        [("selector", "passthrough", [scaler_col])], remainder="drop"
                    ),
                ),
                ("scaler", scaler),
            ]
        )

        transformer = FeatureUnion(
            transformer_list=[
                ("text_feature", txt_pipeline),
                ("label_feature", label_pipeline),
                ("amt_feature", amt_pipeline),
            ]
        )
        transformed_features = transformer.fit_transform(train_df, y)
        X = transformed_features

        # X_train, X_val, y_train, y_val = train_test_split(X,y,stratify=y)
        clf = RandomForestClassifier(**clf_config["rfc_param"])
        # clf.fit(X_train, y_train)
        clf.fit(X, y)

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
                test_transformed_features = transformer.transform(df_cleansed)
                y_hat = y_encoder.inverse_transform(
                    clf.predict(test_transformed_features)
                )
                df_cleansed["Category"] = y_hat
                df["Category"] = df["Category"].fillna(df_cleansed["Category"])

            if clf_config["enable_col_mapping"] and len(df_match) > 0:
                df_match["Category"] = df_match[clf_config["enable_col_mapping"]].map(
                    cate_map
                )
                df["Category"] = df["Category"].fillna(df_match["Category"])

            df["Type"] = np.nan
            if clf_config["enable_Type_col"]:
                df["Type"] = Type_col_mapping(
                    df["Category"],
                    cate_type_map,
                    clf_config["default_Type_value"],
                )

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
