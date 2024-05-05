[out:json][timeout:30000];
area["name:en"="Kanagawa Prefecture"]->.outer;
area["name:en"="Asahi Ward"]->.inner;
(
  nwr["amenity"="place_of_worship"]["religion"="shinto"](area.inner)(area.outer);
);
out geom;
