[out:json][timeout:30];
area["name:ko"="강남구"]->.outer;
area["name:ko"="서울특별시"]->.inner;
(
  nwr["tourism"="aquarium"](area.inner)(area.outer);
);
out geom;
