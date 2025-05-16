    // assets/custom_swiper.js
    // Ensure the global object exists
    window.dash_clientside = window.dash_clientside || {};

    // Define the 'clientside' namespace and the function within it
    window.dash_clientside.clientside = {
        initializeSwiper: function(children) {
            // Check if running in a browser environment
            if (typeof window === 'undefined' || typeof document === 'undefined') {
                console.log("Not running in a browser environment. Skipping Swiper initialization.");
                return null;
            }

            console.log("initializeSwiper called. Children:", children);

            // Small delay to help ensure DOM elements are ready after callback update
            setTimeout(() => {
                // Target the specific swiper instance within the modal using its ID
                const swiperElement = document.querySelector('#swiper-modal .swiper'); // More specific selector

                if (swiperElement) {
                    console.log("Attempting to initialize or update Swiper on:", swiperElement);
                    // Check if Swiper library is loaded
                    if (typeof Swiper === 'undefined') {
                         console.error("Swiper library is not loaded. Make sure swiper-bundle.min.js is included.");
                         return null;
                    }

                    // Check if the element already has a Swiper instance attached
                    if (!swiperElement.swiper) {
                        console.log("Initializing Swiper...");
                        try {
                            new Swiper(swiperElement, {
                                // Swiper options
                                direction: 'horizontal',
                                loop: false, // Loop is often false for dynamically added slides initially
                                pagination: {
                                    el: '.swiper-pagination', // Selector relative to swiperElement
                                    clickable: true,
                                },
                                navigation: {
                                    nextEl: '.swiper-button-next', // Selector relative to swiperElement
                                    prevEl: '.swiper-button-prev', // Selector relative to swiperElement
                                },
                                observer: true,       // Re-init Swiper when slides change (useful for Dash updates)
                                observeParents: true, // Re-init Swiper when parent nodes change
                                observeSlideChildren: true, // Re-init Swiper when slide children change
                                // Add a specific class to initialized swipers to prevent re-initialization issues
                                // init: (swiper) => { swiper.el.classList.add('swiper-initialized'); },
                            });
                            console.log("Swiper initialized successfully.");
                        } catch (e) {
                            console.error("Swiper initialization failed:", e);
                        }
                    } else {
                        console.log("Swiper already initialized on this element, attempting update.");
                        try {
                            // If Swiper is already initialized, update it to reflect potential changes in slides
                            swiperElement.swiper.update();
                            console.log("Swiper updated.");
                        } catch (e) {
                            console.error("Swiper update failed:", e);
                        }
                    }
                } else {
                    // This might happen briefly before the modal content is fully rendered
                    console.log("Swiper element '#swiper-modal .swiper' not found at this moment.");
                }
            }, 200); // Increased delay slightly, adjust if needed

            // Return null or a value that doesn't cause updates if not necessary
            // For Dash clientside callbacks, returning null or undefined is usually fine
            // if the Output is just a dummy.
            return null;
        }
    };