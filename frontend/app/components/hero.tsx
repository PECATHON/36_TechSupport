import {Link} from "react-router";
export default function Hero() {
    return (
        <>
        <div className="text-black">        
        <h1 className="text-7xl/20 text-center align-middle mt-50"> Understand , Summarize and Analyse <br></br><span 
            className="italic bg-clip-text text-transparent"
            style={{
                background: 'linear-gradient(-45deg, #3b82f6, #8b5cf6, #ec4899, #f59e0b, #10b981)',
                backgroundSize: '400% 400%',
                animation: 'gradientShift 3s ease-in-out infinite',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent'
            }}
        >Anything</span></h1>
        <p className="text-3xl text-center mt-8 mr-2 ml-2 text-gray-600">Upload your document and understand its content with ease.</p>
        <div className="flex justify-center mt-8">
            <Link to="/Notebook"><button className="bg-black text-white py-2 px-18 rounded-xl text-xl">Try Out</button></Link>
            
        </div>
        </div>
        
        <style>{`
            @keyframes gradientShift {
                0% {
                    background-position: 0% 50%;
                }
                50% {
                    background-position: 100% 50%;
                }
                100% {
                    background-position: 0% 50%;
                }
            }
        `}</style>
        </>
    );
}