var Comment = {
    form: document.getElementById('comment_form'),
    reply_form: document.getElementById('comment_reply_form'),

    set_events: () => {
        Array.from(document.getElementsByClassName('reply')).forEach(elem => {
            elem.addEventListener('click', (evt) => {
                let target = evt.target;
                Array.from(document.querySelectorAll('.reply.active')).forEach(active => active.classList.remove('active'))
                target.classList.add('active');
            })
        })

        Array.from(document.querySelectorAll('a.comment_like')).forEach(elem => {
            elem.addEventListener('click', Comment.like);
        })

        Array.from(document.querySelectorAll('a.delete-comment')).forEach(elem => {
            elem.addEventListener('click', Comment._delete);
        })

        Comment.form.onsubmit = Comment.add;
        Comment.reply_form.onsubmit = Comment.add_reply;
    },

    add: (e) => {
        e.preventDefault();
        let project_id = document.getElementById('project_title').getAttribute('project_id');

        fetch_form_data(Comment.form, {project_id: project_id})
        $('#add_comment_modal').modal('hide')
    },

    add_reply: (e) => {
        e.preventDefault();
        let comment_id = document.querySelectorAll('a.reply.active')[0].getAttribute('comment_id');

        fetch_form_data(Comment.reply_form, {comment_id: comment_id})
        $('#add_comment_reply_modal').modal('hide')
    },

    like: (evt) => {
        let target = evt.target;

        socket.emit("comment_like", {comment_id: target.getAttribute('comment_id')})
        socket.on("get_state_comment_like", (json) => {
            if (json.status == "fail")
                $.SOW.core.toast.show('danger', 'Ошибка', json.text, 'top-right', 3000, true)
            else {
                if (json.active)
                    target.firstElementChild.classList.replace('text-dark', 'text-primary')
                else
                    target.firstElementChild.classList.replace('text-primary', 'text-dark')


                if (json.text)
                    $.SOW.core.toast.show('success', 'Успех', json.text, 'top-right', 3000, true)
            }
        })
    },

    _delete: (evt) => {
        let comment_id = evt.target.getAttribute('comment_id')
        fetch('/project/comment/delete/', {
            method: "POST",
            headers: {
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            body: JSON.stringify({comment_id: comment_id}),
        })
        .then(res => {
            if (res.status != 200) {
                console.warn(res);
                $.SOW.core.toast.show('danger', 'Ошибка', 'Что-то пошло не так...', 'top-right', 3000, true)
                return;
            }

            if (res.redirected) {
                window.location.href = res.url
                return;
            }

            return res.json()
        }, err => console.error(err))
        .then(json => {
            if (json.status == "fail")
                $.SOW.core.toast.show('danger', 'Ошибка', json.text, 'top-right', 3000, true)
        })
        .catch(warn => console.warn(warn))
    },

}

socket.on("get_count_comment_like", (json) => {
    let target = document.querySelectorAll('a.comment_like[comment_id="'+json.comment_id+'"]')[0];

    if (json.count !== undefined)
        target.lastElementChild.innerText = json.count
})

socket.on("comment_add", (json) => {
    let target = document.querySelectorAll('div.comment-list')[0],
        count_element = document.querySelectorAll('.count_comments[project_id="'+json.project_id+'"]')[0];

    if (document.getElementById('project_title').getAttribute('project_id') == json.project_id
            && json.html !== undefined) {

        target.innerHTML += json.html
        count_element.innerText = json.count

        Comment.set_events()
        $.SOW.core.utils.init();
        $.SOW.core.lazyload.init('.lazy');

        socket.emit("get_comment_right", {
            project_id: json.project_id,
            comment_id: json.comment_id,
        })

        socket.on("right_to_eraser", (json) => {
            console.log(json)
            let target = document.querySelectorAll('a.delete-comment[comment_id="'+json.comment_id+'"]')[0].parentElement;

            if (document.getElementById('project_title').getAttribute('project_id') == json.project_id
                    && json.comment_id !== undefined) {

                target.classList.remove('hide')
                $.SOW.core.utils.init();
                $.SOW.core.lazyload.init('.lazy');
                Comment.set_events();
            }
        })
    }
})

socket.on("comment_reply_add", (json) => {
    let target = document.querySelectorAll('div.comment-reply-list[comment_id="'+json.comment_id+'"]')[0],
        count_element = document.querySelectorAll('.count_replies[comment_id="'+json.comment_id+'"]')[0];

    if (target !== undefined && json.html !== undefined && count_element !== undefined) {

        target.innerHTML += json.html
        count_element.innerText = json.count;

        $.SOW.core.utils.init();
        $.SOW.core.lazyload.init('.lazy');
        Comment.set_events();
    }
})

socket.on("comment_delete", (json) => {
    let target = document.getElementById('comment-'+json.comment_id),
        count_element = document.querySelectorAll('.count_comments[project_id="'+json.project_id+'"]')[0];

    if (target !== undefined && count_element !== undefined) {
        target.remove();
        count_element.innerText = json.count;

        $.SOW.core.utils.init();
        Comment.set_events();
    }
})

Comment.set_events();