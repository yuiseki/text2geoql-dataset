[out:json][timeout:30];
area["name:en"="Niigata Prefecture"]->.outer;
area["name:en"="Chuo Ward"]->.inner;
(
  nwr["amenity"="place_of_worship"]["religion"="shinto"](area.inner)(area.outer);
);
out geom;
