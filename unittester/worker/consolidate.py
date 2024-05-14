import glob, argparse
import xml.etree.cElementTree as ET

def process_reports(xmlpath):
    # Fetch all XML report files
    xml_files = glob.glob(f"{xmlpath}/*.xml")

    # Process XML report files
    for xml_file in xml_files:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        print(root.tag, root.attrib)

        # for child in root:
        #     if child.tag == "testcase":
        #         print(child.tag, child.attrib)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--path",
        required=True,
        type=str,
    )
    args = parser.parse_args()
    process_reports(args.path)
