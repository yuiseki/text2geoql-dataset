[out:json][timeout:30];
area["name:en"="Shenzhen"]->.outer;
area["name:zh"~"深圳"]->.inner;
(
  nwr["shop"~"bicycle"](area.inner)(area.outer);
);
out geom;
