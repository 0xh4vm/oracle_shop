const fetch_forms = (forms) => {
    forms.forEach(form_obj => {
        const form = document.getElementById(form_obj.id);

        const func = (e) => {
            e.preventDefault();

            let data = {};
            Array.from(form.elements).forEach(elem => {
                data[elem.name] = elem.value
            })

            fetch(form_obj.url, {
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
}

const fetch_form_data = (form, add_data={}) => {
    let data = new FormData();
    Array.from(form.elements).forEach(elem => {
        if (elem.name == '')
            return true;

        if (elem.type == 'file' && elem.files.length > 0)
            Array.from(elem.files).forEach(file => data.append(elem.name, file))
        else
            data.append(elem.name, elem.value)
    })

    Object.keys(add_data).forEach(key => {
        data.append(key, add_data[key])
    })

    fetch(form.action, {
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

const dynamic_scripts = (scripts) => {
    scripts.forEach(script => {
        let tag = document.createElement('script');

        tag.setAttribute('src', script);
        tag.setAttribute('async', '');
        document.body.appendChild(tag);
    })
}