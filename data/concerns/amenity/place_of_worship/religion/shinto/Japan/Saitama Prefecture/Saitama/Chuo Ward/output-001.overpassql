[out:json][timeout:30000];
area["name:en"="Saitama Prefecture"]->.outer;
area["name:en"="Chuo Ward"]->.inner;
(
  nwr["amenity"="place_of_worship"]["religion"="shinto"](area.inner)(area.outer);
);
out geom;
