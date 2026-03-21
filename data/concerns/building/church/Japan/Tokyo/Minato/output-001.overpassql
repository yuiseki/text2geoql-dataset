[out:json][timeout:30];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Minato"]->.inner;
(
  nwr["building"="church"](area.inner)(area.outer);
  nwr["amenity"="place_of_worship"]["religion"="christian"](area.inner)(area.outer);
);
out geom;
