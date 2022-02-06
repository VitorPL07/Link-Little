function copyText(text) {
    navigator.clipboard.writeText(text);
}

function setCookie(cname, cvalue, exdays) {
    const d = new Date();
    d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
    let expires = "expires=" + d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

function getCookie(cname) {
    let name = cname + "=";
    let decodedCookie = decodeURIComponent(document.cookie);
    let ca = decodedCookie.split(';');
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

$(".btn").click(function () {

    if ($(".input-name").val() == "") {
        alert("O campo de url está vazio!")
    } else {
        $(".loading").css("display", "flex");
        var getUrl = $(".input-name").val();
        var token = getCookie("token");
        $.ajax({
            url: `/url/set/${token}?url=${getUrl}`,
            type: "POST",
            success: function (result) {
                if (result.status == 200) {
                    $(".input-name").val("");
                    main();
                }
            }
        })
    }
})

function main() {
    var token = getCookie("token");

    if (token == "") {
        $.ajax({
            url: "/user/create",
            type: "get",
            success: function (result) {
                setCookie("token", result["token"], 30);
            }
        });
        return
    } else {
        setCookie("token", token, 30);
    }

    console.log(token);



    $.ajax({
        url: `/user/get/${token}`,
        type: "post",
        success: function (data) {
            if (data.status == 200) {
                // Remover todos os elementos com essa mesma classe
                $(".table-body-element").remove();

                // Se caso existir algum conteúdo, ele vai listar na Home
                if (data.content.length > 0) {
                    $(".container").css("display", "flex");
                    $(".loading").css("display", "flex");


                    data.content.forEach(element => {
                        var littleUrl = window.location.origin + "/l/" + element.url_final;

                        $(".table-body").prepend(`
                        <tr class="table-body-element">
                            <td>
                                <div class="url-main">
                                    <a target="_blank" href="${element.url_main}">${element.url_main}</a>
                                </div>
                            </td>
                            <td><a target="_blank" href="${littleUrl}">${littleUrl}</a></td>
                            <td>
                                <div>
                                    <button class="button-copy" onclick="copyText('${littleUrl}')">Copy</button>
                                </div>
                            </td>
                        </tr>
                        `)
                    });
                } else {
                    $(".container").css("display", "none");
                }
            }
            console.log(data);
            $(".loading").css("display", "none");
        },
        error: function (data) {
            $(".loading").css("display", "none");
        }
    });


}

main();