[out:json][timeout:30];
area["name:zh"="龙华区"]->.outer;
area["name:en"="Longhua District"]->.inner;
(
  nwr["amenity"="hospital"](area.inner)(area.outer);
);
out geom;
