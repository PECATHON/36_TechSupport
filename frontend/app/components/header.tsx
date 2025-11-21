import {Link} from "react-router";
export default function Header() {
    return(
        <>
        <Link to="/dashboard"><h1 className="absolute text-4xl top-3 left-3"><span className="text-blue-400">USA</span>.</h1></Link>
        </>
    )
}
