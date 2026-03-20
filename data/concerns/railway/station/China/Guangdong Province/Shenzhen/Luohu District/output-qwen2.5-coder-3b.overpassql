[out:json][timeout:30];
area["name:zh"="龙岗区"]->.outer;
area["name:en"="Longgang District"]->.inner;
(
  nwr["public_transport"="station"](area.inner)(area.outer);
);
out geom;
