[out:json][timeout:30];
area["name:en"="Shenzhen"]->.outer;
area["name:zh"="罗湖区"]->.inner;
(
  nwr["amenity"="restaurant"]["cuisine"~"chinese"](area.inner)(area.outer);
);
out geom;
