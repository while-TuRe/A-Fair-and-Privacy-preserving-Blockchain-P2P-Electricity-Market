// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

import "./ERC20.sol";
import "./MarginalPrice.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "hardhat/console.sol";

enum ParticipateChoices { Producer, Consumer }
struct DataContract {
    uint256 quantity;
    uint256 price;
}

struct ElectricityOffer {
    address provider;
    DataContract paper;
}

struct ActiveContract {
    DataContract paper;
    uint    electricity_performed;
    ParticipateChoices choices;
}

contract MeterManagement is MarginalPrice,ERC20, Ownable {
    ElectricityOffer[] public electricity_offers;
    uint256 public electricity_offer_num;
    ElectricityOffer[] public bid_offers;
    uint256 public bid_offer_num;
    mapping(address=>int256)  electricity_balance;
    mapping(address=>ActiveContract) public userToDataContract;

    event Burn(address indexed burner, uint256 value); // Burn tokens based on power consumption from the meters wallet
    event Mint(address indexed to, uint256 amount); // Mint tokens based on power production to the meters wallet

    constructor(string memory name, string memory symbol, uint8 decimals)
        ERC20(name, symbol, decimals)
        Ownable(msg.sender)
    {
        // Mint 100 tokens to msg.sender
        // Similar to how
        // 1 dollar = 100 cents
        // 1 token = 1 * (10 ** decimals)
        // _mint(msg.sender, 100 * 10 ** uint256(decimals));
        console.log("MeterManagement constructor msg.sender is  %s",msg.sender);
    }

  
  /**
   * @dev Burns a specific amount of tokens.
   * @param _value The amount of token to be burned.
   */
    function burn(uint256 _value) public { // Burn tokens from the meter's own wallet [msg.sender]
        require(_value <= balanceOf[msg.sender]);
        // no need to require value <= totalSupply, since that would imply the
        // sender's balance is greater than the totalSupply, which *should* be an assertion failure
        ERC20.burn(msg.sender, _value);
        emit Transfer(msg.sender, address(0), _value);
    }
    
    /**
   * @dev Function to mint tokens to an address, as an owner
   * @param _amount of tokens to mint.
   * @param _recipient address of the minting process
   * @return A boolean that indicates if the operation was successful.
   */    
    function mintTo(uint256 _amount, address _recipient)
        public
        onlyOwner
        returns (bool)
    {
        ERC20._mint(_recipient,_amount);
        emit Mint(_recipient, _amount);
        emit Transfer(address(0), _recipient, _amount);
        return true;
    }

    
    //price should be hash of real price
    function offerSubmit(DataContract memory electrucuty)
        public
    {
        require(CheckTradeExist(msg.sender)==false, "only one trade allow");
        ElectricityOffer memory offer ;
        offer.paper=electrucuty;
        offer.provider = msg.sender;
        if(electricity_offer_num<electricity_offers.length)
        {
            electricity_offers[electricity_offer_num] = offer;
        }
        else
        {
            electricity_offers.push(offer);
        }
        electricity_offer_num = electricity_offer_num+1;
    }

    //price should be hash of real price
    function BidSubmit(DataContract memory bid)
        public
    {
        require(balanceOf[msg.sender] >= bid.price*bid.quantity,"balance not enough");
        require(CheckTradeExist(msg.sender)==false, "only one trade allow");
        ElectricityOffer memory offer ;
        offer.paper=bid;
        offer.provider = msg.sender;
        if(bid_offer_num<bid_offers.length)
        {
            bid_offers[bid_offer_num] = offer;
        }
        else
        {
            bid_offers.push(offer);
        }
        bid_offer_num = bid_offer_num+1;
    }

    function getBalance(address user) public view returns (uint256,int){
        return (balanceOf[user],electricity_balance[user]);
    }

    function addBidBalance(address user,uint256 balance,int electricity) public {
        console.logAddress(user);
        console.log("addBidBalance: balance : %d",balance);
        console.logInt(electricity);
        balanceOf[user] = balanceOf[user] - balance;
        electricity_balance[user] = electricity_balance[user] +electricity;
    }

    function addoOffBalance(address user,uint256 balance,int electricity) public {
        console.logAddress(user);
        console.log("addoOffBalance: balance : %d",balance);
        console.logInt(electricity);
        balanceOf[user] = balanceOf[user] + balance;
        electricity_balance[user] = electricity_balance[user] - electricity;
    }

    function getElectricity() public view returns (int){
        return electricity_balance[msg.sender];
    }

    function settleDataContract()  public onlyOwner
    {
        console.log("electricity_offer_num:%d,bid_offer_num:%d",electricity_offer_num,bid_offer_num);
        console.log("electricity_offers.length:%d,bid_offers.length:%d",electricity_offers.length,bid_offers.length);
        ElectricityOffer[] memory t_electricity_offers = new ElectricityOffer[](electricity_offer_num);
        ElectricityOffer[] memory t_bid_offers = new ElectricityOffer[](bid_offer_num);
        uint i =0;
        uint j;
        for (i = 0; i < electricity_offer_num; i++) {
            t_electricity_offers[i] = electricity_offers[i];
        }
        for (i = 0; i < bid_offer_num; i++) {
            t_bid_offers[i] = bid_offers[i];
        }
        
        sort(t_electricity_offers,electricity_offer_num);
        console.log("sort t_electricity_offers,num:%d",t_electricity_offers.length);
        sort(t_bid_offers,bid_offer_num);
        console.log("sort t_bid_offers,num:%d",t_bid_offers.length);
        uint256  supply = 0;
        uint256 demand = 0;
        uint256  marginal_supply = 0;
        uint256 marginal_demand = 0;
        uint256 max_trading_volume = 0;
        uint256 trading_volume = 0;
        uint256 marginal_price = 0;

        // total demand
        for(j =bid_offer_num-1;;j--)
        {
            console.log("t_bid_offers[%d] price:%d,quantity:%d",j,t_bid_offers[j].paper.price, t_bid_offers[j].paper.quantity);
            demand = demand+t_bid_offers[j].paper.quantity;
            if(j==0){ break;}
        }
        console.log("all demand is %d",demand);
        j=0;
        for (i=0; ; )
        {
            supply = supply+t_electricity_offers[i].paper.quantity;
            console.log("t_electricity_offers[%d] price:%d,quantity:%d",i,t_electricity_offers[i].paper.price,t_electricity_offers[i].paper.quantity);
            for(;j<bid_offer_num;j++)
            {
                if(t_bid_offers[j].paper.price < t_electricity_offers[i].paper.price)
                {
                    demand = demand-t_bid_offers[j].paper.quantity;
                }
                else{ break; }
            }
            if(supply >= demand)
            {
                trading_volume = demand;
            }
            else
            {
                trading_volume = supply;
            }
            if(trading_volume >= max_trading_volume)
            {
                max_trading_volume = trading_volume;
                marginal_supply = supply;
                marginal_demand = demand;
                marginal_price = t_electricity_offers[i].paper.price;
            }
            else    // last price is marginal_price
            {
                i = i-1;
                break;
            }
            if(i+1 < electricity_offer_num){ i++; }
            else{ break; }
        }
        console.log("max_trading_volume:%d,marginal_supply:%d,marginal_demand:%d",max_trading_volume,marginal_supply,marginal_demand);
        ActiveContract memory buildcontract;
        if(marginal_supply >= marginal_demand)
        {
            console.log("1 i:%d,j:%d",i,j);
            uint256 excess_supply = marginal_supply-marginal_demand;
            while(true)
            {
                console.log("2 i:%d,j:%d",i,j);
                if(excess_supply == 0)
                {
                    buildcontract.choices = ParticipateChoices.Producer;
                    buildcontract.electricity_performed =0;
                    buildcontract.paper.quantity = t_electricity_offers[i].paper.quantity;
                    buildcontract.paper.price = marginal_price;
                    userToDataContract[t_electricity_offers[i].provider] = buildcontract;
                }
                else if(t_electricity_offers[i].paper.quantity <= excess_supply)
                {
                    excess_supply =excess_supply-t_electricity_offers[i].paper.quantity;
                }
                else
                {
                    buildcontract.choices = ParticipateChoices.Producer;
                    buildcontract.electricity_performed =0;
                    buildcontract.paper.quantity = t_electricity_offers[i].paper.quantity - excess_supply;
                    buildcontract.paper.price = marginal_price;
                    userToDataContract[t_electricity_offers[i].provider] = buildcontract;
                }
                if(i>0){
                    i--;
                }
                else
                {
                    break;
                }
            }
            for(;j <bid_offer_num;j++)
            {
                console.log("3 i:%d,j:%d",i,j);
                buildcontract.choices = ParticipateChoices.Consumer;
                buildcontract.electricity_performed =0;
                buildcontract.paper.quantity = t_bid_offers[j].paper.quantity;
                buildcontract.paper.price = marginal_price;
                userToDataContract[t_bid_offers[j].provider] = buildcontract;
            }
        }
        else
        {
            uint256 excess_consumer = marginal_demand - marginal_supply;
            for(;j <bid_offer_num;j++)
            {
                console.log("4 i:%d,j:%d",i,j);
                if(excess_consumer == 0)
                {
                    buildcontract.choices = ParticipateChoices.Consumer;
                    buildcontract.electricity_performed =0;
                    buildcontract.paper.quantity = t_bid_offers[j].paper.quantity;
                    buildcontract.paper.price = marginal_price;
                    userToDataContract[t_bid_offers[j].provider] = buildcontract;
                }
                else if(t_bid_offers[j].paper.quantity <= excess_consumer)
                {
                    excess_consumer =excess_consumer-t_bid_offers[j].paper.quantity;
                }
                else
                {
                    buildcontract.choices = ParticipateChoices.Consumer;
                    buildcontract.electricity_performed =0;
                    buildcontract.paper.quantity = t_bid_offers[j].paper.quantity - excess_consumer;
                    buildcontract.paper.price = marginal_price;
                    userToDataContract[t_bid_offers[j].provider] = buildcontract;
                }
            }
            while(true)
            {
                console.log("5 i:%d,j:%d",i,j);
                buildcontract.choices = ParticipateChoices.Producer;
                buildcontract.electricity_performed =0;
                buildcontract.paper.quantity = t_electricity_offers[i].paper.quantity;
                buildcontract.paper.price = marginal_price;
                userToDataContract[t_electricity_offers[i].provider] = buildcontract;
                if(i>0){
                    i--;
                }
                else
                {
                    break;
                }
            }
        }
        electricity_offer_num = 0;
        bid_offer_num = 0;
    }

    // 对 memory 数组进行插入排序的辅助函数
    function sort(ElectricityOffer[] memory arr,uint len) internal pure{
        ElectricityOffer memory temp;
        console.log("sort \r\n");
        bool flag = false;
 
        for (uint i = 0; i < len - 1; i++) {
            for (uint j = 0; j < len - 1 - i; j++) {
                console.log("sort i:%d,j:%d \r\n",i,j);
                if (arr[j].paper.price > arr[j + 1].paper.price) {
                    //进入这个if分支里边，则说明有元素进行了交换
                    //所以将flag=true
                    flag = true;
                    temp = arr[j];
                    arr[j] = arr[j + 1];
                    arr[j + 1] = temp;
                }
            }
            
            //在进行完一轮的排序之后，判断本轮是否发生了元素之间的交换
            //如果没有发生交换，说明数组已经是有序的了，则直接结束排序
            if (!flag) {
                break;
            } else {
                //如果发生了交换，那么在下一轮排序之前将flag再次置为false
                //以便记录下一轮排序的时候是否会发生交换
                flag = false;
            }
        }                        
    }

    function CheckTradeExist(address user) internal view returns (bool){
        uint8 i;
        for(i =0;i< bid_offer_num;i++)
        {
            if(user == bid_offers[i].provider)
            {
                return true;
            }
        }
        for(i =0;i< electricity_offer_num;i++)
        {
            if(user == electricity_offers[i].provider)
            {
                return true;
            }
        }
        return false;
    }

}
