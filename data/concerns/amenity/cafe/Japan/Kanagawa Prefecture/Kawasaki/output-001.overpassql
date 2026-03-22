[out:json][timeout:30];
area["name:en"="Kanagawa Prefecture"]->.outer;
area["name:en"="Kawasaki"]->.inner;
(
  nwr["amenity"="cafe"](area.inner)(area.outer);
);
out geom;