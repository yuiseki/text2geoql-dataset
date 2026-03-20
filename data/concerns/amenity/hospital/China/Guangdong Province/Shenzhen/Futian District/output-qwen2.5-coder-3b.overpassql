[out:json][timeout:30];
area["name:zh"="福田区"]->.outer;
area["name:en"="Futian District"]->.inner;
(
  nwr["amenity"="hospital"](area.inner)(area.outer);
);
out geom;
