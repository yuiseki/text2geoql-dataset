[out:json][timeout:30000];
area["name:en"="Aichi Prefecture"]->.outer;
area["name:en"="Higashi Ward"]->.inner;
(
  nwr["amenity"="place_of_worship"]["religion"="shinto"](area.inner)(area.outer);
);
out geom;
