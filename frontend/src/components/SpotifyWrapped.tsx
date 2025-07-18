import React from "react";


interface SpotifyWrappedData {
	topArtists: Array<{ name: string; image?: string }>;
	topSongs: Array<{ name: string; artist?: string }>;
	topGenre: string;
	timeframe: string; // e.g., "This Year", "Last 6 Months", "All Time"
	topArtistImage?: string;
}

interface SpotifyWrappedCardProps {
	data: SpotifyWrappedData;
}

export default function SpotifyWrappedCard({ data }: SpotifyWrappedCardProps) {
	const { topArtists, topSongs, topGenre, timeframe, topArtistImage } = data;

	// Use the first artist's image or fallback to a default
	const mainArtistImage =
		topArtistImage ||
		topArtists[0]?.image ||
		"https://i.scdn.co/image/ab6761610000e5ebd1b2c17ca08f1fc22e4a90b6";

	return (
		<div
			className="w-[430px] h-[765px] flex items-center justify-center bg-[#fa5dc7] rounded-2xl shadow-2xl overflow-hidden mx-auto"
			style={{ transform: "scale(0.8)", transformOrigin: "top left" }}
		>
			<div className="w-[400px] h-[700px] flex flex-col items-center pt-1">
				{/* Pattern with artist image overlapping */}
				<div className="relative flex flex-col items-center">
					<img
						src="/pattern1.png"
						alt="Spotify Wrapped Pattern"
						className="w-88 h-88 object-contain"
						draggable={false}
					/>
					{/* Artist image overlays pattern, centered */}
					<div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-57 h-57 bg-white flex items-center justify-center overflow-hidden">
						<img
							src={mainArtistImage}
							alt="Top Artist"
							className="object-cover w-full h-full"
						/>
					</div>
				</div>
				{/* Stats Section */}
				<div className="w-full mt-8 px-6 lato-regular">
					<div className="grid grid-cols-2 gap-8 text-black">
						{/* Top Artists */}
						<div>
							<div className="text-xl mb-2 tracking-wide">Top Artists</div>
							<ul className="lato-black text-xl">
								{topArtists.map((artist, i) => (
									<li key={i} className="truncate flex items-center">
										<span className="text-lg mr-2">{i + 1}</span> {artist.name}
									</li>
								))}
							</ul>
						</div>
						{/* Top Songs */}
						<div>
							<div className="text-xl mb-2 tracking-wide">Top Songs</div>
							<ul className="lato-black text-xl">
								{topSongs.map((song, i) => (
									<li key={i} className="truncate flex items-center">
										<span className=" mr-2">{i + 1}</span>
										{song.name}
									</li>
								))}
							</ul>
						</div>
					</div>
					{/* Genre */}
					<div className="flex justify-between items-center mt-6 text-base text-black">
						<div>
							<div className="text-xl ">Top Genre</div>
							<div className="text-3xl lato-black">{topGenre}</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	);
}
