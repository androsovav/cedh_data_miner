import { Link, createSearchParams } from "react-router-dom";

import { colorImages, cardIcon } from "../images/index";
import { compressObject } from "../utils";

export default function Entry({
  enableLink,
  slug,
  rank,
  name,
  mox,
  metadata,
  colors,
  tournament,
  metadata_fields,
  layout = 'default',
  filters
}) {
  return (
    <tr className={`grid ${layout === 'default' ? "" : ""} grid-cols-3 grid-rows-2 md:table-row text-cadet dark:text-white text-lg rounded-lg shadow-modal py-2 sm:py-0 md:[&>td]:py-3 `}>
      {rank ? <td className="hidden md:table-cell text-lightText dark:text-text">{rank}</td> : <></>}

      {name ? (
        <td className="col-start-1 col-span-2 font-semibold">
          {enableLink ? (
            <Link to={`${slug}${filters.standing || filters.tourney_filter ? "?" + createSearchParams(compressObject({
                ...(filters.tourney_filter && {tourney_filter: filters.tourney_filter}), 
                ...(filters.standing && {standing: filters.standing}),
              })) : ""}`}>
              <span className="cursor-pointer" href="">
                {rank && <span className="text-sm text-lightText dark:text-text md:hidden">
                  #{rank}{' '}
                </span>}
                {name}{' '}
                <span className="text-sm text-text md:hidden">
                  ({metadata[metadata.length - 1]})
                </span>
              </span>
            </Link>
          ) : (
            <span className="flex items-center gap-1 text-lg font-semibold">
              {rank && <span className="text-sm text-lightText dark:text-text md:hidden">
                #{rank}{' '}
              </span>}
              <a href={mox} target="_blank" rel="noreferrer">
                {name}
                <img className="ml-2 w-6 inline" src={cardIcon} alt="mox" />
              </a>
              <span className="text-sm text-lightText dark:text-text md:hidden">
                ({metadata[metadata.length - 1]})
              </span>
            </span>
          )}
        </td>
      ) : (
        <></>
      )}

      {metadata ? metadata.map((data, i, a) => <td className="hidden md:table-cell">{data}</td>) : <></>}
      {metadata && layout === 'default' ? metadata.map((data, i, a) => i < a.length - 1 && <td className="flex md:hidden col-start-3 text-sm justify-end">{metadata_fields[i]}: {data}</td>) : <></>}
      {metadata && layout === 'WLD' ? <td className="flex md:hidden col-start-3 text-sm justify-end">St / W / L / D</td> : <></>}
      {metadata && layout === 'WLD' ? <td className="flex md:hidden col-start-3 row-start-2 text-sm justify-end">{metadata.filter((data, i, a) => i < a.length - 1).join(' / ')}</td> : <></>}

      {colors ? (
        <td className="flex flex-wrap px-2 gap-2 !m-0 align-middle [&>img]:w-5 md:[&>img]:w-6 col-start-1 col-span-2 row-start-2">
          {colors.split("").map((color) => {
            if (["W", "U", "B", "R", "G", "C"].includes(color)) {
              return <img key={color} src={colorImages[color]} alt={color} />;
            }
          })}
        </td>
      ) : (
        <></>
      )}

      {tournament ? <td className="flex col-start-1 col-span-2 md:table-cell text-sm">{tournament}</td> : <></>}
    </tr>
  );
}
