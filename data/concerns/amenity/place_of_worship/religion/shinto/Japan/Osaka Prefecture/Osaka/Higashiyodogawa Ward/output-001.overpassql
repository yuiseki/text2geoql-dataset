[out:json][timeout:30000];
area["name:en"="Osaka Prefecture"]->.outer;
area["name:en"="Higashiyodogawa Ward"]->.inner;
(
  nwr["amenity"="place_of_worship"]["religion"="shinto"](area.inner)(area.outer);
);
out geom;
