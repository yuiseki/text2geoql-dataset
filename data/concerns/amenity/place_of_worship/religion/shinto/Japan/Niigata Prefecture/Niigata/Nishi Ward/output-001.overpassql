[out:json][timeout:30000];
area["name:en"="Niigata Prefecture"]->.outer;
area["name:en"="Nishi Ward"]->.inner;
(
  nwr["amenity"="place_of_worship"]["religion"="shinto"](area.inner)(area.outer);
);
out geom;
