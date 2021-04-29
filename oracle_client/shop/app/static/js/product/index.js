const socket = io();

var ProductCard = {
    set_events: () => {
        Array.from(document.getElementsByClassName('like_product')).forEach(button => {
            button.addEventListener('click', ProductCard.like)
        })

        Array.from(document.getElementsByClassName('dislike_product')).forEach(button => {
            button.addEventListener('click', ProductCard.dislike)
        })

        Array.from(document.getElementsByClassName('to_cart')).forEach(button => {
            button.addEventListener('click', ProductCard.to_cart)
        })

        Array.from(document.getElementsByClassName('remove')).forEach(button => {
            button.addEventListener('click', ProductCard.remove)
        })

        Array.from(document.getElementsByClassName('edit')).forEach(button => {
            button.addEventListener('click', ProductCard.edit)
        })

        document.getElementById('edit_product').addEventListener('click', ProductCard.edit_product);
        
        if (document.getElementById('buy') != null)
            document.getElementById('buy').addEventListener('click', ProductCard.buy_products);

        if (document.getElementById('unlock') != null) {
            document.getElementById('unlock').addEventListener('click', () => {
                fetch("/product/unlock/", {   
                    method: "POST",
                    headers: {
                        "Accept": "application/json",
                        "Content-Type": "application/json"
                    },
                })
                .then(res => {
                    if (res.status != 200) {
                        console.warn(res);
                        $.SOW.core.toast.show('danger', 'Ошибка', 'Что-то пошло не так...', 'top-right', 3000, true)
                        return;
                    }
                }, err => console.error(err))
                .catch(warn => console.warn(warn))
            });
        }
        
    },

    carcass: (target, action) => {
        let product_id = target.getAttribute('product_id')

        socket.emit(action, {product_id: product_id})
        socket.on("get_state_"+action, (json) => {
            if (json.status == "fail")
                $.SOW.core.toast.show('danger', 'Ошибка', json.text, 'top-right', 3000, true)
            else {
                let t = document.querySelector('a.'+action+'_product[product_id="'+json.product_id+'"]');
                if (json.active) {
                    t.classList.replace('bg-white', 'bg-danger')
                    t.firstElementChild.classList.replace('text-dark', 'text-white')
                }
                else {
                    t.classList.replace('bg-danger', 'bg-white')
                    t.firstElementChild.classList.replace('text-white', 'text-dark')
                }

                if (json.text)
                    $.SOW.core.toast.show('success', 'Успех', json.text, 'top-right', 3000, true)
            }
        })
    },

    like: (evt) => {
        let dislike = document.querySelector('a.dislike_product[product_id="'+evt.target.getAttribute('product_id')+'"]');

        if (dislike.classList.contains('bg-danger'))
            ProductCard.carcass(dislike, 'dislike')

        ProductCard.carcass(evt.target, 'like')
    },

    dislike: (evt) => {
        let like = document.querySelector('a.like_product[product_id="'+evt.target.getAttribute('product_id')+'"]');

        if (like.classList.contains('bg-danger'))
             ProductCard.carcass(like, 'like')

        ProductCard.carcass(evt.target, 'dislike')
    },

    remove: (evt) => {
        let cart = evt.target;

        fetch("/product/remove/", {
            method: "POST",
            headers: {
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            body: JSON.stringify({product_id: cart.getAttribute('product_id')}),
        })
        .then(res => {
            if (res.status != 200) {
                console.warn(res);
                $.SOW.core.toast.show('danger', 'Ошибка', 'Что-то пошло не так...', 'top-right', 3000, true)
                return;
            }
            
            return res.json()
        }, err => console.error(err))
        .then(json => {
            if (json.status == "fail")
                $.SOW.core.toast.show('danger', 'Ошибка', json.text, 'top-right', 3000, true)
            
            document.getElementById('product-'+cart.getAttribute('product_id')).remove();

            if (json.text)
                $.SOW.core.toast.show('success', 'Успех', json.text, 'top-right', 3000, true)
        })
        .catch(warn => console.warn(warn))
    },

    to_cart: (evt) => {
        let cart = evt.target,
        product_id = cart.getAttribute('product_id'),
        version = document.querySelector('.version[product_id="'+product_id+'"]').innerText;

        fetch("/product/to_cart/", {
            method: "POST",
            headers: {
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            body: JSON.stringify({product_id: product_id, version:version}),
        })
        .then(res => {
            if (res.status != 200) {
                console.warn(res);
                $.SOW.core.toast.show('danger', 'Ошибка', 'Что-то пошло не так...', 'top-right', 3000, true)
                return;
            }
            
            return res.json()
        }, err => console.error(err))
        .then(json => {
            if (json.status == "fail") {
                $.SOW.core.toast.show('danger', 'Ошибка', json.text, 'top-right', 3000, true)
                return;
            }
        
            if (json.count_cart != undefined && json.count_cart != null && parseInt(json.count_cart) >= 0)
                document.getElementById('count-products-in-cart').innerText = json.count_cart;

            if (json.active) {
                cart.classList.replace('bg-white', 'bg-danger')
                cart.firstElementChild.classList.replace('text-dark', 'text-white')

                /* document.getElementById('count-products-in-cart').innerText++;*/
                
                document.getElementById('item-list').innerHTML += '<div id="'+json.product.id+
                '" class="item clearfix d-block px-3 py-3 border-top">'+
                '<div class="h--50 overflow-hidden float-start mt-1">'+
                '<img src="/static/products/'+json.product.image+'" alt="..." width="40">'+
                '</div>'+
                '<a href="#!" class="fs--15 d-block position-relative">'+
                '<span class="d-block text-truncate">'+
                json.product.title+' ('+json.product.author+')</span></a>'+
                '<span class="d-block fs--12 mt-1">'+json.product.cost+' руб.</span>'+
                '</div>';
                document.getElementById('cost-all').innerText = parseInt(document.getElementById('cost-all').innerText) + parseInt(json.product.cost);
                document.getElementById('cost-all').innerText += ' руб.';
                
            } else {
                cart.classList.replace('bg-danger', 'bg-white')
                cart.firstElementChild.classList.replace('text-white', 'text-dark')
                
                /* document.getElementById('count-products-in-cart').innerText--;*/
                document.getElementById(json.product.id).remove()
                document.getElementById('cost-all').innerText = parseInt(document.getElementById('cost-all').innerText) - parseInt(json.product.cost);
                document.getElementById('cost-all').innerText += ' руб.';

            }
            $.SOW.core.toast.show('success', 'Успех', json.text, 'top-right', 3000, true)
        })
        .catch(warn => console.warn(warn))
    },

    edit: (evt) => {
        fetch("/product/lock_edit/", {   
            method: "POST",
            headers: {
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            body: JSON.stringify({product_id: evt.target.getAttribute('product_id')}),
        })
        .then(res => {
            if (res.status != 200) {
                console.warn(res);
                $.SOW.core.toast.show('danger', 'Ошибка', 'Что-то пошло не так...', 'top-right', 3000, true)
                return;
            }
            
            return res.json()
        }, err => console.error(err))
        .then(json => {
            if (json.status == "fail") {
                $.SOW.core.toast.show('danger', 'Ошибка', json.text, 'top-right', 3000, true)
                document.getElementById('product_title').value = '';
                document.getElementById('product_author').value = '';
                document.getElementById('product_description').value = '';
                document.getElementById('product_cost').value = '';
            }
            else {
                if (json.product != undefined && json.product != null) {
                    document.getElementById('product_id').value = json.product.id;
                    document.getElementById('product_title').value = json.product.title;
                    document.getElementById('product_author').value = json.product.author;
                    document.getElementById('product_description').value = json.product.description;
                    document.getElementById('product_cost').value = json.product.cost;
                }
            }
        })
        .catch(warn => console.warn(warn))
    },

    edit_product: () => {
        let data = {
            product_id: document.getElementById('product_id').value,
            new_title: document.getElementById('product_title').value,
            new_author: document.getElementById('product_author').value,
            new_description: document.getElementById('product_description').value,
            new_cost: parseInt(document.getElementById('product_cost').value) > 0 ? parseInt(document.getElementById('product_cost').value) : 0,
        };

        fetch("/product/edit/", {   
            method: "POST",
            headers: {
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data),
        })
        .then(res => {
            if (res.status != 200) {
                console.warn(res);
                $.SOW.core.toast.show('danger', 'Ошибка', 'Что-то пошло не так...', 'top-right', 3000, true)
                return;
            }
            
            return res.json()
        }, err => console.error(err))
        .then(json => {
            if (json.status == "fail")
                $.SOW.core.toast.show('danger', 'Ошибка', json.text, 'top-right', 3000, true)
            else
                window.location.reload();
        })
        .catch(warn => console.warn(warn))
    },

    buy_products: () => {
        let cart = document.getElementById('item-list'),
            data = {};
           
        Array.from(cart.children).forEach(item => {
            data[item.id] = {id: item.id, version:document.querySelector('.version[product_id="'+item.id+'"]').innerText}
        });

        console.log(data);
        fetch("/product/buy/", {   
            method: "POST",
            headers: {
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data),
        })
        .then(res => {
            if (res.status != 200) {
                console.warn(res);
                $.SOW.core.toast.show('danger', 'Ошибка', 'Что-то пошло не так...', 'top-right', 3000, true)
                return;
            }
            
            return res.json()
        }, err => console.error(err))
        .then(json => {
            if (json.status == "fail")
                $.SOW.core.toast.show('danger', 'Ошибка', json.text, 'top-right', 3000, true)
            else
                $.SOW.core.toast.show('success', 'Успех', json.text, 'top-right', 3000, true)
        })
        .catch(warn => console.warn(warn))
    }
}

ProductCard.set_events()

let actions = ['like', 'dislike'];

actions.forEach(action => {
    socket.on("get_count_"+action, (json) => {
        let target = document.querySelector('a.'+action+'_product[product_id="'+json.product_id+'"]');

        if (json.count !== undefined)
            target.lastElementChild.innerText = json.count
    })
})
