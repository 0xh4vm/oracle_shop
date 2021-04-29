var Account = {
    forms:  [{id: 'form_account', url:'/auth/account/change_settings/'}],

    set_events: () => {
        document.getElementById('remove_avatar').addEventListener('click', () => {
            let avatar = document.getElementById('remove_avatar').nextElementSibling.firstElementChild;
            avatar.style['background-image'] = ""

            document.querySelectorAll("input[name='remove_avatar']")[0].value = true
        })

        document.getElementById('remove_project').addEventListener('click', () => {
            let button = document.querySelectorAll('.remove_project.selected')[0];

            fetch('/project/remove/', {
                method: "POST",
                headers: {
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    project_id: button.getAttribute('project_id')
                }),
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
                else {
                    button.parentElement.parentElement.parentElement.remove();
                    $.SOW.core.toast.show('success', 'Успех', json.text, 'top-right', 3000, true)
                }
            })
            .catch(warn => console.warn(warn))
        })

        Account.change_settings_form_submit(Account.forms)

        Account.remove_project();
    },

    change_settings_form_submit: (forms) => {
        forms.forEach(form_obj => {
            const form = document.getElementById(form_obj.id);

            const func = (e) => {
                e.preventDefault();

                let data = new FormData();
                Array.from(form.elements).forEach(elem => {
                    if (elem.type == 'file' && elem.files.length > 0)
                        data.append(elem.name, elem.files[0])
                    else
                        data.append(elem.name, elem.value)
                })

                fetch(form_obj.url, {
                    method: "POST",
                    body: data,
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
            }

            form.onsubmit = func
        })
    },

    remove_project: () => {
        Array.from(document.getElementsByClassName('remove_project')).forEach(button => {
            button.addEventListener('click', (evt) => {
                let target = evt.target;

                Array.from(document.getElementsByClassName('selected')).forEach(project => {
                    project.classList.remove('selected')
                });

                target.classList.add('selected');
            })
        })
    },

}

Account.set_events();