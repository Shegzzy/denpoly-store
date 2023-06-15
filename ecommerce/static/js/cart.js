var updateBtns = document.getElementsByClassName('update-cart');

for (var i = 0; i < updateBtns.length; i++) {
    updateBtns[i].addEventListener('click', function (event) {
        event.preventDefault();
        var productId = this.dataset.product;
        var action = this.dataset.action;
        console.log('productId:', productId, 'action:', action);

        console.log('USER:', user);
        if (user == 'AnonymousUser') {
            addCookieItem(productId, action);
        } else {
            updateUserOrder(productId, action);
        }
    });
}

function addUpdateCartListeners() {
    var updateBtns = document.getElementsByClassName('update-cart');

    for (var i = 0; i < updateBtns.length; i++) {
        updateBtns[i].addEventListener('click', function (event) {
            event.preventDefault();
            var productId = this.dataset.product;
            var action = this.dataset.action;
            console.log('productId:', productId, 'action:', action);

            console.log('USER:', user);
            if (user == 'AnonymousUser') {
                addCookieItem(productId, action);
            } else {
                updateUserOrder(productId, action);
            }

        });
    }
}

function addCookieItem(productId, action) {
    console.log('Guest user...');

    if (action === 'add') {
        if (cart[productId] === undefined) {
            cart[productId] = { 'quantity': 1 };
        } else {
            cart[productId]['quantity'] += 1;
        }
        showPopupMessage('Item added to cart');
    }
    if (action === 'remove') {
        cart[productId]['quantity'] -= 1;

        if (cart[productId]['quantity'] <= 0) {
            console.log('Item removed');
            delete cart[productId];
            removeCartItem(productId);
            showPopupMessage('Item removed from cart');

        }

    }

    if (action === 'delete') {
        cart[productId]['quantity'] = 0;
        delete cart[productId];
        deleteCartItem(productId);
        showPopupMessage('Item deleted from cart');
    }


    console.log('Cart:', cart);
    document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/";

    const cartCountElement = document.getElementById('cart-count');
    const totalQuantity = Object.values(cart).reduce((acc, item) => acc + item.quantity, 0);
    cartCountElement.textContent = totalQuantity;

    fetch('/cart_data/')
        .then(response => response.json())
        .then(data => {
            const cartTotalElement = document.getElementById('cart-total');
            cartTotalElement.textContent = '₦' + data.order.get_cart_total;

            const cartsTotalElement = document.getElementById('carts-total');
            if (cartsTotalElement) {
                cartsTotalElement.textContent = '₦' + data.order.get_cart_total;
            }

            const miniCartTotalElement = document.getElementById('mini-cart-total');
            if (miniCartTotalElement !== null) {
                if (data.order && data.order.get_cart_total) {
                    miniCartTotalElement.textContent = '₦' + data.order.get_cart_total;
                } else {
                    miniCartTotalElement.textContent = '₦0';
                }
            }

            const cartsCountElement = document.getElementById('carts-count');
            if (cartsCountElement) {
                cartsCountElement.textContent = data.cartItems;
            }

            const itemsQuantityElement = document.getElementById(`cart-items-quantity-${productId}`);
            if (itemsQuantityElement && data.items[productId] && data.items[productId].quantity !== undefined) {
                itemsQuantityElement.value = data.items[productId].quantity;

                if (data.items[productId].quantity <= 0) {
                    removeCartItem(productId); // Remove the item from the DOM
                }
            }

            const itemsQuantityField = document.getElementById(`miniCart_item-quantity-${productId}`);
            if (itemsQuantityField && data.items[productId] && data.items[productId].quantity !== undefined) {
                itemsQuantityField.textContent = data.items[productId].quantity;
            }

            if (data.items[productId] && data.items[productId].quantity <= 0) {
                removeCartItems(productId);
            }

            const itemsAmountElement = document.getElementById(`item-amount-${productId}`);
            if (itemsAmountElement && data.items[productId] && data.items[productId].get_total !== undefined) {
                itemsAmountElement.textContent = '₦' + data.items[productId].get_total;
            }

            const miniCartItemsElement = document.getElementById('mini-cart-items');
            if (miniCartItemsElement) {
                miniCartItemsElement.innerHTML = data.miniCartHTML;
            }
        })
        .catch(error => console.error('Error:', error));
}

function updateUserOrder(productId, action) {
    console.log('user is logged in as:', user);
    var url = '/update_item/';

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({ 'productId': productId, 'action': action }),
    })

        .then((response) => {
            console.log(response);
            return response.json();
        })

        .then((data) => {
            console.log('data:', data);
            const cartCountElement = document.getElementById('cart-count');
            cartCountElement.textContent = data.cartItems;

            const cartsCountElement = document.getElementById('carts-count');
            if (cartsCountElement) {
                cartsCountElement.textContent = data.cartItems;
            }

            const cartTotalElement = document.getElementById('cart-total');
            cartTotalElement.textContent = '₦' + data.cartTotal;

            const miniCartTotalElement = document.getElementById('mini-cart-total');
            if (miniCartTotalElement) {
                miniCartTotalElement.textContent = '₦' + data.cartTotal;
            }

            const cartsTotalElement = document.getElementById('carts-total');
            if (cartsTotalElement) {
                cartsTotalElement.textContent = '₦' + data.cartTotal;
            }

            const itemsQuantityElement = document.getElementById(`cart-items-quantity-${productId}`);
            if (itemsQuantityElement) {
                itemsQuantityElement.value = data.itemsQuantity;
            }

            if (data.itemsQuantity <= 0) {
                removeCartItem(productId); // Remove the item from the DOM
            }

            const itemsQuantityField = document.getElementById(`miniCart_item-quantity-${productId}`);
            if (itemsQuantityField) {
                itemsQuantityField.textContent = data.itemsQuantity;
            }

            if (data.itemsQuantity <= 0) {
                removeCartItems(productId); // Remove the item from the DOM
            }

            const itemsAmountElement = document.getElementById(`item-amount-${productId}`);
            if (itemsAmountElement) {
                itemsAmountElement.textContent = '₦' + data.productTotal;
            }

            const miniCartItemsElement = document.getElementById('mini-cart-items');
            if (miniCartItemsElement) {
                miniCartItemsElement.innerHTML = data.miniCartHTML;
            }
            showPopupMessage(data.message[0])
        });
}

function removeCartItem(productId) {
    const itemElement = document.getElementById(`cart-items-quantity-${productId}`);
    if (itemElement && itemElement.closest('tr')) {
        const itemHolder = itemElement.closest('tr');
        itemHolder.remove();
    }
}


function removeCartItems(productId) {
    const itemContainer = document.getElementById(`item-container-${productId}`);
    if (itemContainer) {
        const miniItemHolder = itemContainer.closest('li');
        if (miniItemHolder) {
            miniItemHolder.remove();
        }
    }
}


function deleteCartItem(productId) {
    var url = user === 'AnonymousUser' ? '/cart_data/' : '/update_item/';
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({ 'productId': productId, 'action': 'delete' }),
    })
        .then((response) => {
            console.log(response);
            return response.json();
        })
        .then((data) => {
            console.log('data:', data);

            removeCartItems(productId);
            removeCartItem(productId);

        })
        .catch((error) => {
            console.error('Error:', error);
        });
}

// Function to handle tab switching
$('#categories-tab').on('click', '.category-link', function (e) {
    e.preventDefault();  // Prevent the default link behavior

    // Remove the 'active' class from all category links
    $('.category-link').removeClass('active');

    // Add the 'active' class to the clicked category link
    $(this).addClass('active');

    // Get the target tab ID from the data attribute
    var targetTabId = $(this).data('target');

    // Hide all tab panes
    $('.tab-pane').removeClass('active');
    $('.tab-pane').css('opacity', 0);

    // Show the target tab pane with animation
    $(targetTabId).addClass('active');
    setTimeout(function () {
        $(targetTabId).css('opacity', 1);
    }, 50);

    // Hide the product section with animation
    $('#products-section').removeClass('show');

    // Fetch and replace the product data for the selected category
    var categorySlug = $(this).attr('href').split('=')[1];
    var url = '/get-products/?category=' + categorySlug;

    $.ajax({
        url: url,
        type: 'GET',
        success: function (data) {
            $('#products-section').html($(data).find('#products-section').html());
            addUpdateCartListeners();

            $('.pagination').html($(data).find('.pagination').html());
        },
        error: function (xhr, textStatus, errorThrown) {
            console.log('Error:', errorThrown);
        }
    });
});

$(document).on('click', '.pagination .previous-page, .pagination .next-page', function (e) {
    e.preventDefault();  // Prevent the default link behavior

    var url = $(this).attr('href');

    $.ajax({
        url: url,
        type: 'GET',
        success: function (data) {
            $('#products-section').html($(data).find('#products-section').html());
            addUpdateCartListeners();

            $('.pagination').html($(data).find('.pagination').html());

            // Scroll to the top of the products section
            $('html, body').animate({ scrollTop: $('#products-section').offset().top }, 'slow');
        },
        error: function (xhr, textStatus, errorThrown) {
            console.log('Error:', errorThrown);
        }
    });
});



function showPopupMessage(message) {
    console.log('Showing popup message');
    var popupMessage = document.getElementById('popup-message');
    var popupMessageText = document.getElementById('popup-message-text');

    if (popupMessage && popupMessageText) {
        popupMessageText.textContent = message;
        popupMessage.classList.add('show');

        // Hide the popup message after a certain duration
        setTimeout(function () {
            hidePopupMessage();
        }, 3000); // Adjust the duration as desired
    }
}

function hidePopupMessage() {
    var popupMessage = document.getElementById('popup-message');
    if (popupMessage) {
        popupMessage.classList.remove('show');
    }
}

