[out:json][timeout:30000];
area["name:en"="Kyoto Prefecture"]->.outer;
area["name:en"="Higashiyama Ward"]->.inner;
(
  nwr["amenity"="place_of_worship"]["religion"="shinto"](area.inner)(area.outer);
);
out geom;
