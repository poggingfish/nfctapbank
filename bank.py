import network as ps
import tx as transaction
import json
def tx(path,addr):
    y = ps.extract_path(path)[1:]
    if float(y[2]) < 0.01:
        return ps.basic_http_html + "Fail"
    if len(str(float(y[2])).split(".")[1]) > 2:
        return ps.basic_http_html + "Fail"
    return ps.basic_http_html + transaction.tx(y[0],y[1],float(y[2])) + """<script>
setTimeout(function(){
    window.location.href = "about:blank"
}, 3500);
</script>"""
def card(path,addr):
    x = json.load(open("bank.json"))
    if ps.extract_path(path)[0] not in x:
        return ps.basic_http_html + "Card not found"
    Server.new_var("bal",str(x[ps.extract_path(path)[0]]["balance"]))
    return ps.basic_http_html + Server.get_website("front.html")

Server = ps.Server("192.168.69.186",4449)
Server.add_path_function_wildcard("/v1/card/",tx)
Server.add_path_function_wildcard("/card/",card)
Server.add_path_redirect("/","index.html")
Server.listen()