[out:json][timeout:30];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Kozushima"]->.inner;
(
  nwr["amenity"="place_of_worship"]["religion"="shinto"](area.inner)(area.outer);
);
out geom;
