lightbox = window.localStorage.getItem("lightbox_1")
if lightbox:
    lightbox = JSON.parse(lightbox)
else:
    lightbox = []

manifests = []
for anitem in lightbox:
    manifests.append(
        {
            "manifestId": document.SITE_URL
            + "/api/iiif/presentation/"
            + anitem
            + "/info.json"
        }
    )
console.log(manifests)

mirador = Mirador.viewer({"id": "amirador", "catalog": manifests})
