console.log('hello world from cart.js!')
var updateBtns = document.getElementsByClassName('update-cart')

// sends button actions to the backend.  Frontend is updated on refresh
for (i=0; i < updateBtns.length; i++) {
    updateBtns[i].addEventListener('click', function(){
        var productId = this.dataset.product
        var action = this.dataset.action
        console.log('productId:',productId, 'Action:', action)

        console.log('USER:', user)
        if (user == 'AnonymousUser'){
            addCookieItem(productId, action)
        }else{
            console.log('User is authenticated, sending data...')
            updateUserOrder(productId, action)
        }
    })
}

function addCookieItem(productId, action){
    console.log('User is not authenticated')

    if (action == 'add'){
        if (cart[productId] == undefined){
            cart[productId] = {'quantity':1};
        }else{
            cart[productId]['quantity'] += 1
        }
    }

    if (action == 'remove'){
        cart[productId]['quantity'] -= 1
        
        if (cart[productId]['quantity'] <= 0){
            console.log('Remove Item')
            delete cart[productId]
        }
    }

    console.log('Cart: ', cart)
    document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/"
    location.reload() //reloads page, remove for debugging to see logs to console.
}

// only updates on refreshing.
function updateUserOrder(productId, action){
    console.log("order function triggered")
    var url = '/update_item/'
    
    //fetch is a service worker
    //needs method, headers and body to send to backend
    fetch(url, {
        method: 'POST',
        headers:{
            'Content-Type': 'application/json',
            'X-CSRFToken' : csrftoken,
        },
        body: JSON.stringify({'productId': productId, 'action': action})
    })

    //once the backend responds the .then() does another step
    .then((response) =>{
        return response.json()
    })

    .then((data) =>{
        console.log('data: ', data)
    })
}