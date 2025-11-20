import { useState } from "react";
import * as ALL from "C:/Users/SWARNIM ARYA/36_TechSupport/backend/output/images";
export default function Upload() {
  const [files, setFiles] = useState<File[]>([]);
  const [pdfUrls, setPdfUrls] = useState<string[]>([]);
  const [isUploaded, setIsUploaded] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(e.target.files ?? []).filter(
      (f) => f.type === "application/pdf"
    );
    if (selectedFiles.length > 0) {
      setFiles(selectedFiles);
      const urls = selectedFiles.map((f) => URL.createObjectURL(f));
      setPdfUrls(urls);
      uploadPdfs(selectedFiles);
      setIsUploaded(true);
    }
  };

  const uploadPdfs = async (pdfs: File[]) => {
    const formData = new FormData();
    pdfs.forEach((p) => formData.append("files", p));

    // Example: send to backend that accepts multiple files under the `files` key
    // const res = await fetch("http://127.0.0.1:8000/ingest_pdfs", {
    //   method: "POST",
    //   body: formData,
    // });
    // const data = await res.json();
    // console.log("Upload response:", data);

  };

  return (
    <>
      {!isUploaded ? (
        <div className="flex justify-center mt-50 gap-6">
          <div className="w-1/2">
            <label className="cursor-pointer flex flex-col items-center justify-center border-2 border-dashed border-blue-400 p-10 rounded-lg bg-linear-to-r from-blue-300 to-purple-300 opacity-80 hover:opacity-100 transition">
              <span className="text-5xl text-blue-400 bg-white w-16 h-16 flex items-center justify-center rounded-full border shadow-lg mb-4">
                +
              </span>
              <h1 className="text-xl font-bold text-blue-700">
                Upload your document
              </h1>
              <input
                type="file"
                accept="application/pdf"
                onChange={handleFileChange}
                hidden
                multiple
              />
            </label>
          </div>
        </div>
      ) : (
        <div className="overflow-y-scroll flex flex-col md:flex-row mt-20 mr-10 ml-10 gap-4">
          <div className="w-auto h-[80vh] flex-1">
            {/* {pdfUrls.length > 0 ? (
              <iframe
                src={pdfUrls[0] || undefined}
                className="w-[85vh] h-full border rounded-lg"
                title={`PDF Preview 0`}
              />
            ) : null} */}

          </div>
          <div className="w-64 flex flex-col gap-4 overflow-y-auto">
            {pdfUrls.map((url, idx) => (
              <div key={idx} className="border rounded p-2 bg-white">
                <a href={url} target="_blank" rel="noreferrer" className="text-sm text-blue-600">
                  Document {idx + 1}
                </a>
                <div className="mt-2">
                  <iframe src={url} title={`pdf-thumb-${idx}`} className="w-full h-40 border rounded" />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </>
  );
}