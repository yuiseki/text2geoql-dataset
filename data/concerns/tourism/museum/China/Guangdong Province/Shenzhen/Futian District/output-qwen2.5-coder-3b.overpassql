[out:json][timeout:30];
area["name:zh"="深圳市"]->.outer;
area["name:zh"="福田区"]->.inner;
(
  nwr["tourism"="museum"](area.inner)(area.outer);
);
out geom;
