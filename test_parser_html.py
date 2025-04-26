from web2 import WebScrapping

html_text_1 = """
    <!DOCTYPE html>
    <div class="container">
    </div>
    <div class="row">
        <div class="col-md-4"> <!-- Commentaire -->
            <h2>Gmail <!-- Commentaire --></h2>
            <p>Gmail is a free email service developed by Google.</p>
        </div>
        <div class="col-md-4">
            <h2>Yahoo</h2>
            <p>Yahoo is a web services provider.</p>
        </div>
        <div class="col-md-4">
            <h2>Outlook</h2>
            <p>Outlook is a personal information manager from Microsoft.</p>
        </div>
    </div>
"""

if __name__ == "__main__":
    a = WebScrapping()

    elements = a.get_html_elements(html_text=html_text_1)
    assert len(elements) == 14, "Test failed: Expected 14 elements, got {}".format(len(elements))

    arguments = a.get_arguments(("div", 'class="container de test" id="main"'))
    assert arguments == ("div", {'class': 'container de test', 'id': 'main'}), "Test failed: Expected ('div', {'class': 'container de test', 'id': 'main'}), got {}".format(arguments)
    print("All tests passed!")
