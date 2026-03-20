[out:json][timeout:30];
area["name:zh"="盐田区"]->.outer;
area["name:en"="Yantian District"]->.inner;
(
  nwr["amenity"="hospital"](area.inner)(area.outer);
);
out geom;
