[out:json][timeout:30];
area["name:zh"="深圳市"][boundary=administrative]->.outer;
area["name:en"="Shenzhen"]->.inner;
(
  nwr["amenity"="cafe"](area.inner)(area.outer);
);
out geom;
