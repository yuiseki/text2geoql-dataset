[out:json][timeout:30];
area["name:ko"="서울특별시"]->.outer;
area["name:ko"="송파구"]->.inner;
(
  nwr["tourism"="aquarium"](area.inner)(area.outer);
);
out geom;
