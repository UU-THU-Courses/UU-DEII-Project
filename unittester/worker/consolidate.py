import glob, argparse
import xml.etree.cElementTree as ET

def process_reports(xmlpath):
    # Fetch all XML report files
    xml_files = glob.glob(f"{xmlpath}/*.xml")
    final_report = {
        "time": 0,
        "tests": 0,
        "errors": 0,
        "skipped": 0,
        "failures": 0,
    }
    # Process XML report files
    for xml_file in xml_files:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Consolidate all report files
        final_report["tests"] += int(root.attrib["tests"])
        final_report["errors"] += int(root.attrib["errors"])
        final_report["skipped"] += int(root.attrib["skipped"])
        final_report["failures"] += int(root.attrib["failures"])
        final_report["time"] += float(root.attrib["time"])
        
        # for child in root:
        #     if child.tag == "testcase":
        #         print(child.tag, child.attrib)

    print(final_report)    
    return final_report

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--path",
        required=True,
        type=str,
    )
    args = parser.parse_args()
    process_reports(args.path)
