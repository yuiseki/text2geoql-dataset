[out:json][timeout:30000];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Shinjuku"]->.inner;
(
  nwr["amenity"="place_of_worship"]["religion"="shinto"](area.inner)(area.outer);
);
out geom;
