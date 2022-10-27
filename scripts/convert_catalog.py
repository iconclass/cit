#!/usr/bin/env python
import os, argparse
import xml.etree.ElementTree as ET
import textbase
from rich.progress import track


def parse(CIT_data, filename, HIM, images):
    # Note, parsing file: CIT export_inOrder_04.03.2019.xml 20190312 gives error in XML on lines 781763 and 781765 encountering character  '\x02' embedded in file.
    # Looks like all the source have this so do a search and replace to fix it.
    # Object with <sys_id>O1455666</sys_id> has no vanda_museum_number ?
    # Some objects, like cit_O1466337 doesnot the associated jpg yet?

    filecontents = (
        open(filename, encoding="utf8")
        .read()
        .replace(
            "^vandap34_object_display_hours_calc", "vandap34_object_display_hours_calc"
        )
    )
    doc = ET.fromstring(filecontents)
    objs = []

    for item in track(doc.findall(".//mus_catalogue")):
        sys_id = item.find(".//sys_id")
        if sys_id.text is None:
            print(obj)
            break

        obj = {
            "ID": ["cit_%s" % sys_id.text],
            "HIM": ["CIT", HIM],
            "COL": [HIM],
            "TYPE": ["image"],
            "LOCATION.INV": ["Victoria and Albert Museum"],
        }
        name = item.find(".//mus_object_name/_")
        if name is not None:
            obj["DESCRIPTION"] = [name.text]

        spec_title_field = item.find(".//spec_title_field")
        if spec_title_field is not None:
            obj["TITLE"] = [spec_title_field.text]

        for mus_obj_images_field_data in item.findall(".//mus_obj_images_field_data"):
            image_filename = mus_obj_images_field_data.text
            if not image_filename.endswith(".jpg"):
                image_filename = "%s.jpg" % mus_obj_images_field_data.text
            obj.setdefault("URL.IMAGE", []).append(image_filename)

        # Note only import items with valid CIT IDs as classifiers.
        # https://chineseiconography.org/r/view/cit_O68886/vanda

        cit_list_id = []
        # And do all the CIT terms, but retain their IDs.
        for spec_content_other in item.findall(".//spec_content_other/_"):
            spec_content_other_field_val = spec_content_other.find(
                ".//spec_content_other_field_val"
            )
            if (
                spec_content_other_field_val is not None
                and spec_content_other_field_val.text
            ):
                # Only look for the cit id if we also have a val for it, so do it inside the if
                spec_content_other_field_th_i = spec_content_other.find(
                    ".//spec_content_other_field_th_i"
                )
                if (
                    spec_content_other_field_th_i is not None
                    and spec_content_other_field_th_i.text
                ):
                    cit_id = spec_content_other_field_th_i.text
                    if cit_id in CIT_data:
                        cit_list_id.append(cit_id)

        if cit_list_id:
            obj["CIT"] = cit_list_id

        mapping = {
            ".//mus_part_obj_num_display": "ID.INV.ALT",
            ".//spec_object_production_date_note": "DATE",
            ".//spec_object_production_date_field_text": "DATE",
            ".//spec_other_number_field": "INSTIT.INV",
            ".//spec_other_number_type/spec_other_number_type_val": "ID.INV.INST",
            ".//spec_object_production_person_field_data": "PERSON.ARTIST",
            ".//spec_object_production_person_association_val": "PERSON.ROLE",
            ".//spec_reference_details": "LOCATION.INV",
            ".//mus_reference_free": "URL.WEBPAGE",
            ".//vanda_museum_number": "ID.INV.ALT",
        }
        for path, field in mapping.items():
            val = item.find(path)
            if val is not None and val.text:
                obj[field] = list(filter(None, val.text.split("\n")))

        # For the NPM and MET the REF field contains the URL.IMAGE,
        # For VandA entries it should be
        # 'http://collections.vam.ac.uk/item/' + sys_id.text
        if HIM == "VANDA":
            obj["URL.WEBPAGE"] = ["http://collections.vam.ac.uk/item/" + sys_id.text]

        # The NPM JPG filenames are what is in the 'INSTIT.INV' field with a .jpg appended
        # if HIM == "NPM":
        #    INSTIT_INV = obj.get("INSTIT.INV")
        #    if INSTIT_INV:
        #        obj["URL.IMAGE"] = [f"{x.strip()}.jpg" for x in INSTIT_INV]

        # For some exported items, the image filenames are NOT in .//mus_obj_images_field_data
        # but need to be extracted from .//vanda_museum_number :-(
        if "URL.IMAGE" not in obj:
            vanda_museum_number = obj.get("ID.INV.ALT", [None])[0]
            vanda_museum_number_image = f"{vanda_museum_number}.jpg"
            obj["URL.IMAGE"] = [vanda_museum_number_image.strip()]

        skip_object = True
        images = [
            image_filename
            for image_filename in obj.get("URL.IMAGE", [])
            if image_filename in images
        ]
        if len(images) < 1:
            continue
        obj["URL.IMAGE"] = images

        objs.append(obj)

    return objs


def dump(filename, objs):
    print(f"Saving {len(objs)} objects")
    with open(filename, "w", encoding="utf8") as F:
        for obj in objs:
            for k, v in obj.items():
                tmp = "\n; ".join(set(v))
                F.write("%s %s\n" % (k, tmp))
            F.write("$\n")


def main(filepaths, collection, imagespath):
    images = set(
        [
            filename
            for dirpath, dirnames, filenames in os.walk(imagespath)
            for filename in filenames
        ]
    )

    CIT_data = {}
    for x in textbase.parse("CIT.dmp"):
        CIT_data[x["ID"][0]] = x

    CAT_data = {}
    if os.path.exists("CATALOG.dmp"):
        for x in textbase.parse("CATALOG.dmp"):
            CAT_data[x["ID"][0]] = x

    new_count = 0
    for filepath in filepaths:
        for x in parse(CIT_data, filepath, collection, images):
            new_count += 1
            CAT_data[x["ID"][0]] = x
    print(f"Read {new_count} for this file")

    dump("CATALOG.dmp", CAT_data.values())


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "inputfiles",
        nargs="+",
        help="The XML file(s) to read from",
    )
    argparser.add_argument(
        "-c",
        "--collection",
        required=True,
        help="Which Collection does this file belong to?",
        choices=["VANDA", "MET", "NPM", "HYL", "CMA"],
    )
    argparser.add_argument(
        "-i",
        "--images",
        required=True,
        help="Location of the images folder to check if a .jpg file exists",
    )

    args = argparser.parse_args()
    main(args.inputfiles, args.collection, args.images)
