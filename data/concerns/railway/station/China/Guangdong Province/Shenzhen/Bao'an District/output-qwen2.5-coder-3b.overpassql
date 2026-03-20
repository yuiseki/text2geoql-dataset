[out:json][timeout:30];
area["name:zh"="宝安区"]->.outer;
area["name:en"="Bao'an District"]->.inner;
(
  nwr["railway"="station"](area.inner)(area.outer);
);
out geom;
