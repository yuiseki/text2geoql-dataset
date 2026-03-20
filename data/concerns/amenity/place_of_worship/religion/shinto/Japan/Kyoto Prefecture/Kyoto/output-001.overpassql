[out:json][timeout:30];
area["name:en"="Kyoto Prefecture"]->.outer;
area["name:en"="Kyoto"]->.inner;
(
  nwr["amenity"="place_of_worship"]["religion"="shinto"](area.inner)(area.outer);
);
out geom;
