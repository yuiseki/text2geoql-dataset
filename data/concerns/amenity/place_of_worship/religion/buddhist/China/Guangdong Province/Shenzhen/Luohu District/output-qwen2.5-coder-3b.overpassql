[out:json][timeout:30];
area["name:zh"="罗湖区"]->.outer;
area["name:en"="Luohu District"]->.inner;
(
  nwr["building"~"temple"](area.inner)(area.outer);
);
out geom;
