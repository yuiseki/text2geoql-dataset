[out:json][timeout:30000];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Meguro"]->.inner;
(
  nwr["amenity"="place_of_worship"]["religion"="buddhist"](area.inner)(area.outer);
);
out geom;
