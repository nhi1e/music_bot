import React, { useRef } from "react";
import { toPng } from "html-to-image";

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
const bgOptions = [
	{ bg: "bg-[#121212]", pattern: "/pattern_black.png", text: "text-[#f2fe48]" },
	{ bg: "bg-[#fa5dc7]", pattern: "/pattern_pink.png", text: "text-[#121212]" },
	{
		bg: "bg-[#f2ff46]",
		pattern: "/pattern_yellow.png",
		text: "text-[#121212]",
	},
];

export default function SpotifyWrappedCard({ data }: SpotifyWrappedCardProps) {
	const { topArtists, topSongs, topGenre, timeframe, topArtistImage } = data;
	const componentRef = useRef<HTMLDivElement>(null);

	// Generate a unique key for each wrapped request to force new randomization
	const uniqueKey = `${timeframe}-${topGenre}-${topArtists[0]?.name || "unknown"}-${Date.now()}`;

	// Generate new theme each time based on unique key
	const getRandomTheme = () => {
		const randomIndex = Math.floor(Math.random() * bgOptions.length);
		return bgOptions[randomIndex];
	};

	// Always generate a fresh theme on each render
	const currentTheme = getRandomTheme();

	// Use the first artist's image or fallback to a default
	const mainArtistImage =
		topArtistImage ||
		topArtists[0]?.image ||
		"https://i.scdn.co/image/ab6761610000e5ebd1b2c17ca08f1fc22e4a90b6";

	const { bg, pattern, text } = currentTheme;

	const downloadImage = async () => {
		if (componentRef.current) {
			try {
				const dataUrl = await toPng(componentRef.current, {
					quality: 1.0,
					pixelRatio: 2, // Higher quality
				});

				// Create download link
				const link = document.createElement("a");
				link.download = `spotify-wrapped-${timeframe.toLowerCase().replace(/\s+/g, "-")}.png`;
				link.href = dataUrl;
				link.click();
			} catch (error) {
				console.error("Error generating image:", error);
			}
		}
	};

	return (
		<div className="relative">
			<div
				ref={componentRef}
				className={`w-[430px] h-[765px] flex items-center justify-center ${bg} rounded-2xl shadow-2xl overflow-hidden`}
				style={{ transform: "scale(0.8)", transformOrigin: "top left" }}
			>
				<div className="w-[400px] h-[700px] flex flex-col items-center pt-1">
					{/* Pattern with artist image overlapping */}
					<div className="relative flex flex-col items-center">
						<img
							src={pattern}
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
						<div className={`grid grid-cols-2 gap-8 ${text}`}>
							{/* Top Artists */}
							<div>
								<div className="text-xl mb-2 tracking-wide">Top Artists</div>
								<ul className="lato-black text-xl">
									{topArtists.map((artist, i) => (
										<li key={i} className="truncate flex items-center">
											<span className="text-lg mr-2">{i + 1}</span>{" "}
											{artist.name}
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
						<div
							className={`flex justify-between items-center mt-6 text-base ${text}`}
						>
							<div>
								<div className="text-xl ">Top Genre</div>
								<div className="text-3xl lato-black">{topGenre}</div>
							</div>
						</div>
					</div>
				</div>
			</div>

			{/* Download Button */}
			<button
				onClick={downloadImage}
				className="absolute top-2 right-2 bg-white/20 hover:bg-white/30 text-white px-3 py-1 rounded-md text-sm transition-colors"
				title="Download as image"
			>
				💾 Save
			</button>
		</div>
	);
}
