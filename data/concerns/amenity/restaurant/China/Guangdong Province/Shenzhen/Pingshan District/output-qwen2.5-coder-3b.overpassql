[out:json][timeout:30];
area["name:zh"="深圳市"][boundary=administrative]->.outer;
area["name:zh"="龙岗区"]->.inner;
(
  nwr["amenity"~"restaurant"](area.inner)(area.outer);
);
out geom;
