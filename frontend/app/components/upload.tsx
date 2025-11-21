import { useState } from "react";

type ImageData = {
  csvUrl: string;
  imageUrl: string;
  description: string;
};

type UploadResponse = {
  csvs: [string, string, string][];
  images: [string, string, string][];
};

export default function Upload() {
  const [file, setFile] = useState<File | null>(null);
  const [pdfUrl, setPdfUrl] = useState<string>("");
  const [isUploaded, setIsUploaded] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [csvData, setCsvData] = useState<ImageData[]>([]);
  const [imageData, setImageData] = useState<ImageData[]>([]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      const url = URL.createObjectURL(selectedFile);
      setPdfUrl(url);
      uploadPdf(selectedFile);
      setIsUploaded(true);
    }
  };

  const uploadPdf = async (pdf: File) => {
    setIsLoading(true);
    const formData = new FormData();
    formData.append("file", pdf);

    try {
      const res = await fetch("http://127.0.0.1:8000/upload", {
        method: "POST",
        body: formData,
      });
      const data: UploadResponse = await res.json();
      
      // Transform the data
      const csvs = data.csvs.map(([csvUrl, imageUrl, description]) => ({
        csvUrl,
        imageUrl,
        description,
      }));
      
      const images = data.images.map(([csvUrl, imageUrl, description]) => ({
        csvUrl,
        imageUrl,
        description,
      }));
      
      setCsvData(csvs);
      setImageData(images);
    } catch (error) {
      console.error("Upload error:", error);
    } finally {
      setIsLoading(false);
    }
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
                accept="application/pdf,image/*"
                onChange={handleFileChange}
                hidden
              />
            </label>
          </div>
        </div>
      ) : (
        <div className="overflow-y-scroll flex flex-row mt-10 mr-10 ml-10 gap-6">
          {isLoading ? (
            <div className="flex justify-center items-center h-64">
              <div className="text-xl text-blue-600">Processing document...</div>
            </div>
          ) : (
            <>
              {/* PDF Preview Section */}
              {pdfUrl && (
                <div className="w-full h-[60vh] border rounded-lg overflow-hidden">
                  <iframe
                    src={pdfUrl}
                    className="w-full h-full"
                    title="PDF Preview"
                  />
                </div>
              )}

              {/* CSV Tables Section */}
              {csvData.length > 0 && (
                <div className="mt-6">
                  <h2 className="text-2xl font-bold text-gray-800 mb-4">
                    Tables from Document
                  </h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {csvData.map((item, idx) => (
                      <div
                        key={idx}
                        className="border rounded-lg p-4 bg-white shadow-md"
                      >
                        <h3 className="text-lg font-semibold text-gray-700 mb-2">
                          Table {idx + 1}
                        </h3>
                        {item.imageUrl && (
                          <img
                            src={item.imageUrl}
                            alt={`Table ${idx + 1}`}
                            className="w-full h-auto mb-3 border rounded"
                          />
                        )}
                        <p className="text-sm text-gray-600 mb-2">
                          {item.description}
                        </p>
                        {item.csvUrl && (
                          <a
                            href={item.csvUrl}
                            target="_blank"
                            rel="noreferrer"
                            className="text-blue-600 hover:underline text-sm"
                          >
                            Download CSV
                          </a>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Charts Section */}
              {imageData.length > 0 && (
                <div className="mt-6">
                  <h2 className="text-2xl font-bold text-gray-800 mb-4">
                    Charts from Document
                  </h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {imageData.map((item, idx) => (
                      <div
                        key={idx}
                        className="border rounded-lg p-4 bg-white shadow-md"
                      >
                        <h3 className="text-lg font-semibold text-gray-700 mb-2">
                          Chart {idx + 1}
                        </h3>
                        {item.imageUrl && (
                          <img
                            src={item.imageUrl}
                            alt={`Chart ${idx + 1}`}
                            className="w-full h-auto mb-3 border rounded"
                          />
                        )}
                        <p className="text-sm text-gray-600 mb-2">
                          {item.description}
                        </p>
                        {item.csvUrl && (
                          <a
                            href={item.csvUrl}
                            target="_blank"
                            rel="noreferrer"
                            className="text-blue-600 hover:underline text-sm"
                          >
                            Download CSV Data
                          </a>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </>
  );
}