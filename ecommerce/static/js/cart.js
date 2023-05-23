var updateBtns = document.getElementsByClassName('update-cart')

for (var i = 0; i < updateBtns.length; i++) {
    updateBtns[i].addEventListener('click', function (event) {
        event.preventDefault();
        var productId = this.dataset.product
        var action = this.dataset.action
        console.log('productId:', productId, 'action:', action)

        console.log('USER:', user)
        if (user == 'AnonymousUser') {
            addCookieItem(productId, action)
        } else {
            updateUserOrder(productId, action)
        }

    })
}

function addCookieItem(productId, action) {
    console.log('Guest user...')

    if (action === 'add') {
        if (cart[productId] === undefined) {
            cart[productId] = { 'quantity': 1 };
        } else {
            cart[productId]['quantity'] += 1;
        }
    }
    if (action === 'remove') {
        cart[productId]['quantity'] -= 1;

        if (cart[productId]['quantity'] <= 0) {
            console.log('Item removed');
            delete cart[productId];
        }
    }

    if (action === 'delete') {
        cart[productId]['quantity'] === 0;
        delete cart[productId]
        deleteCartItem(productId)
        // Remove the item from the DOM
    }

    console.log('Cart:', cart)
    document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/"

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
            if (data.order && data.order.get_cart_total) {
                miniCartTotalElement.textContent = '₦' + data.order.get_cart_total;
            } else {
                miniCartTotalElement.textContent = '₦0';
            }

            const cartsCountElement = document.getElementById('carts-count');
            if (cartsCountElement) {
                cartsCountElement.textContent = data.cartItems;
            }

            const itemsQuantityElement = document.getElementById(`items-quantity-${productId}`);
            if (itemsQuantityElement && data.items[productId] && data.items[productId].quantity !== undefined) {
                itemsQuantityElement.value = data.items[productId].quantity;
            }

            if (data.items[productId] && data.items[productId].quantity <= 0) {
                removeCartItem(productId);
            }

            const itemsQuantityField = document.getElementById(`item-quantity-${productId}`);
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
        })
        .catch(error => console.error('Error:', error));
}

function updateUserOrder(productId, action) {
    console.log('user is logged in as:', user)
    var url = '/update_item/'

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({ 'productId': productId, 'action': action, 'cart': cart }),
    })

        .then((response) => {
            console.log(response);
            return response.json()
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
        });
}

function removeCartItem(productId) {
    const itemElement = document.getElementById(`cart-items-quantity-${productId}`).closest('tr');
    if (itemElement) {
        delete itemElement;
        itemElement.remove();
    }
}

function removeCartItems(productId) {
    const itemContainer = document.getElementById(`item-container-${productId}`);
    if (itemContainer) {
        delete itemContainer;
        itemContainer.remove();
    }
}

function deleteCartItem(productId) {
    fetch('/update_item/', {
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
            // Update the cart UI accordingly
            const itemHolder = document.getElementById(`item-container-${productId}`);
            if (itemHolder) {
                itemHolder.remove();
            }

            const itemElement = document.getElementById(`cart-items-quantity-${productId}`).closest('tr');
            if (itemElement) {
                itemElement.remove();
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
}


