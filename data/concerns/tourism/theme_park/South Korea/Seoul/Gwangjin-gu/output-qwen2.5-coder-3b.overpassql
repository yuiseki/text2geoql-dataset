[out:json][timeout:30];
area["name:ko"="서울특별시"]->.outer;
area["name:ko"="광진구"]->.inner;
(
  nwr["tourism"="theme_park"](area.inner)(area.outer);
);
out geom;
