[out:json][timeout:30];
area["name:en"="Kanagawa Prefecture"]->.outer;
area["name:en"="Sakae Ward"]->.inner;
(
  nwr["amenity"="place_of_worship"]["religion"="shinto"](area.inner)(area.outer);
);
out geom;
