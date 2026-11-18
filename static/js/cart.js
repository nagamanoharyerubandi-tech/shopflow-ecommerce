/**
 * ShopFlow - Cart AJAX Operations
 */

document.addEventListener('DOMContentLoaded', function () {
    // 1. Quick Add to Cart via AJAX
    document.querySelectorAll('.ajax-add-to-cart').forEach(function (button) {
        button.addEventListener('click', function (e) {
            e.preventDefault();
            const url = this.getAttribute('data-url');
            const originalContent = this.innerHTML;

            this.disabled = true;
            this.innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span> Adding...';

            fetch(url, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                }
            })
            .then(response => response.json().then(data => ({ status: response.status, body: data })))
            .then(({ status, body }) => {
                this.disabled = false;
                this.innerHTML = originalContent;

                if (body.success) {
                    showToast(body.message, 'success');
                    updateCartBadge(body.cart_total_items);
                } else {
                    showToast(body.message || 'Could not add product.', 'danger');
                }
            })
            .catch(error => {
                this.disabled = false;
                this.innerHTML = originalContent;
                showToast('Something went wrong. Please try again.', 'danger');
            });
        });
    });

    // 2. Cart Page Dynamic Quantity Controls
    document.querySelectorAll('.cart-qty-btn').forEach(function (button) {
        button.addEventListener('click', function (e) {
            e.preventDefault();
            const action = this.getAttribute('data-action');
            const itemId = this.getAttribute('data-item-id');
            const updateUrl = this.getAttribute('data-url');

            fetch(`${updateUrl}?action=${action}`, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                }
            })
            .then(response => response.json().then(data => ({ status: response.status, body: data })))
            .then(({ status, body }) => {
                if (body.success) {
                    updateCartBadge(body.cart_total_items);

                    if (body.item_quantity === 0) {
                        // Item was removed
                        const row = document.getElementById(`cart-row-${itemId}`);
                        if (row) {
                            row.remove();
                        }
                    } else {
                        // Update item quantity and item total
                        const qtySpan = document.getElementById(`qty-val-${itemId}`);
                        const totalSpan = document.getElementById(`item-total-${itemId}`);
                        if (qtySpan) qtySpan.textContent = body.item_quantity;
                        if (totalSpan) totalSpan.textContent = `₹${body.item_total}`;
                    }

                    // Update summary numbers
                    const subtotalElem = document.getElementById('cart-summary-subtotal');
                    const shippingElem = document.getElementById('cart-summary-shipping');
                    const taxElem = document.getElementById('cart-summary-tax');
                    const grandTotalElem = document.getElementById('cart-summary-grand-total');

                    if (subtotalElem) subtotalElem.textContent = `₹${body.cart_subtotal}`;
                    if (shippingElem) shippingElem.textContent = body.cart_shipping === '0.00' ? 'FREE' : `₹${body.cart_shipping}`;
                    if (taxElem) taxElem.textContent = `₹${body.cart_tax}`;
                    if (grandTotalElem) grandTotalElem.textContent = `₹${body.cart_grand_total}`;

                    if (body.cart_total_items === 0) {
                        window.location.reload();
                    }
                } else {
                    showToast(body.message, 'warning');
                }
            })
            .catch(error => {
                showToast('Failed to update cart quantity.', 'danger');
            });
        });
    });
});

function updateCartBadge(count) {
    const badge = document.getElementById('header-cart-badge');
    if (badge) {
        badge.textContent = count;
        badge.style.display = count > 0 ? 'inline-block' : 'none';
    }
}
