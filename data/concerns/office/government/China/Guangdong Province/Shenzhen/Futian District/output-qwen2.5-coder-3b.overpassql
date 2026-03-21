[out:json][timeout:30];
area["name:zh"="福田区"]->.outer;
area["name:zh"="深圳市"]->.inner;
(
  nwr["office"~"government"](area.inner)(area.outer);
);
out geom;
